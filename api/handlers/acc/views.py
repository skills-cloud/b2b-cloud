import itertools
from functools import partial

from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.encoding import force_text
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, status, mixins, serializers, parsers
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django_filters import rest_framework as filters

from main import models as main_models
from acc.models import User
from api.backends import FilterBackend
from api.filters import OrderingFilterNullsLast, ModelMultipleChoiceCommaSeparatedFilter
from api.serializers import StatusSerializer
from api.permissions import AllowAny, IsAuthenticated
from api.views import ViewSetFilteredByUserMixin, ReadWriteSerializersMixin
from api.handlers.acc import serializers as acc_serializers

__all__ = [
    'openapi_response_user',
    'openapi_response_guest',
    'LoginView',
    'LogoutView',
    'WhoAmIView',
    'WhoAmISetPhotoView',
    'SetTimezone',
    'UserManageViewSet',
]

openapi_response_user = partial(openapi.Response, 'If the user is logged in')
openapi_response_guest = partial(openapi.Response, "If the user isn't logged in")


class LoginView(generics.GenericAPIView):
    serializer_class = acc_serializers.LoginSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response('If it is OK', StatusSerializer()),
            status.HTTP_403_FORBIDDEN: openapi.Response('If credentials is not OK', StatusSerializer()),
        }
    )
    def post(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=False)
        if settings.DEBUG:
            user = User.objects.filter(email=request_serializer.data.get('email')).first()
        else:
            user = authenticate(
                request,
                username=request_serializer.data.get('email'),
                password=request_serializer.data.get('password')
            )
        if user:
            response_data = {'status': 'ok'}
            response_status = status.HTTP_200_OK
            login(self.request, user)
        else:
            response_data = {'status': 'error', 'details': 'Bad email or password'}
            response_status = status.HTTP_403_FORBIDDEN
        response_serializer = StatusSerializer(data=response_data)
        response_serializer.is_valid()
        return Response(response_serializer.data, status=response_status)


class LogoutView(generics.GenericAPIView):
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='It authorizes the user',
        responses={
            status.HTTP_200_OK: openapi_response_guest(acc_serializers.WhoAmISerializer()),
            status.HTTP_403_FORBIDDEN: openapi_response_user(StatusSerializer()),
        }
    )
    def post(self, request, *args, **kwargs):
        logout(request)
        response_serializer = StatusSerializer(data={'status': 'ok'})
        response_serializer.is_valid()
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class WhoAmIView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    http_method_names = ['get', 'patch']
    queryset = User.objects.all()
    serializer_class = acc_serializers.WhoAmISerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Регистрационные данные текущего пользователя',
        responses={
            status.HTTP_200_OK: openapi_response_guest(acc_serializers.WhoAmISerializer()),
            status.HTTP_403_FORBIDDEN: openapi_response_user(StatusSerializer()),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description='Изменение регистрационных данных текущего пользователя',
        responses={
            status.HTTP_200_OK: openapi_response_guest(acc_serializers.WhoAmISerializer()),
            status.HTTP_403_FORBIDDEN: openapi_response_user(StatusSerializer()),
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        return super().get_queryset().get(id=self.request.user.id)


class WhoAmISetPhotoView(WhoAmIView):
    http_method_names = ['post']
    parser_classes = [parsers.MultiPartParser]
    serializer_class = acc_serializers.UserSetPhotoSerializer

    @swagger_auto_schema(
        operation_description='Изменение поля фото (`photo`) текущего пользователя',
        responses={
            status.HTTP_200_OK: openapi_response_guest(acc_serializers.WhoAmISerializer()),
            status.HTTP_403_FORBIDDEN: openapi_response_user(StatusSerializer()),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, instance=self.request.user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(acc_serializers.WhoAmISerializer(
            instance=self.request.user,
            context=self.get_serializer_context()
        ).data, status=status.HTTP_200_OK)


class SetTimezone(generics.GenericAPIView):
    serializer_class = acc_serializers.SetTimeZoneSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(''),
        }
    )
    def post(self, request, *args, **kwargs):
        request.session['timezone'] = self.get_serializer(request.data).data['time_zone']
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class UserManageViewSet(ViewSetFilteredByUserMixin, ReadWriteSerializersMixin, ModelViewSet):
    class Filter(filters.FilterSet):
        organization_contractor_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationContractor.objects,
            field_name='organizations_contractors_roles__organization_contractor'
        )
        organization_project_id = ModelMultipleChoiceCommaSeparatedFilter(
            queryset=main_models.OrganizationProject.objects,
            field_name='organizations_projects_roles__organization_project'
        )

    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = User.objects.prefetch_related(
        'organizations_contractors_roles', 'organizations_contractors_roles__organization_contractor',
        'organizations_projects_roles', 'organizations_projects_roles__organization_project',
        'organizations_projects_roles__organization_project__organization_customer',
    )
    serializer_class = acc_serializers.UserManageSerializer
    serializer_read_class = acc_serializers.UserManageReadSerializer
    filter_backends = [FilterBackend, OrderingFilterNullsLast, SearchFilter]
    filterset_class = Filter
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'first_name', 'last_name', 'email']
    ]))
    ordering = ['last_name', 'first_name', 'id']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'organization_contractor_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False
            ),
            openapi.Parameter(
                'organization_project_id',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description='`ANY`',
                required=False
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, enum=ordering_fields),
                default=ordering,
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


########################################################################################################################
# ПОКА НЕ НУЖНО
########################################################################################################################


class RegistrationView(generics.CreateAPIView):
    class Serializer(acc_serializers.UserSerializer):
        class Meta(acc_serializers.UserSerializer.Meta):
            exclude = None
            fields = ['id', 'email', 'password', 'last_name', 'first_name']

        def save(self, **kwargs):
            self.instance = super().save(**kwargs)
            self.instance.set_password(self.data['password'])
            self.instance.save()
            return self.instance

    queryset = User.objects.all()
    serializer_class = Serializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            k: v
            for k, v in response.data.items() if k != 'password'
        }
        return response


class PasswordResetView(generics.GenericAPIView):
    class Serializer(serializers.Serializer):
        email = serializers.EmailField()
        password_reset_form_class = PasswordResetForm
        html_email_template_name = 'email/password-reset/email.html'

        def validate_email(self, value):
            self.reset_form = self.password_reset_form_class(data=self.initial_data)
            if not self.reset_form.is_valid():
                raise serializers.ValidationError(self.reset_form.errors)

            if not list(self.reset_form.get_users(self.reset_form.cleaned_data["email"])):
                raise NotFound(str(_('User %s not found.' % value)))

            return value

        def save(self):
            request = self.context.get('request')
            opts = {
                'use_https': request.is_secure(),
                'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
                'request': request,
                'html_email_template_name': self.html_email_template_name,
            }
            self.reset_form.save(**opts)

        class Meta:
            extra_kwargs = {
                'name': {
                    'validators': [],
                }
            }

    serializer_class = Serializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': 'ok',
            "details": str(_(
                "We've emailed you instructions for setting your password, if an account exists with the email you "
                "entered. You should receive them shortly."
            ))
        })


class PasswordResetConfirmView(generics.GenericAPIView):
    class Serializer(serializers.Serializer):
        new_password1 = serializers.CharField(max_length=128)
        new_password2 = serializers.CharField(max_length=128)
        uid = serializers.CharField()
        token = serializers.CharField()

        set_password_form_class = SetPasswordForm

        def validate(self, attrs):
            self._errors = {}

            try:
                uid = force_text(uid_decoder(attrs['uid']))
                self.user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                raise ValidationError({'uid': ['Invalid value']})

            self.set_password_form = self.set_password_form_class(
                user=self.user, data=attrs
            )
            if not self.set_password_form.is_valid():
                raise serializers.ValidationError(self.set_password_form.errors)
            if not default_token_generator.check_token(self.user, attrs['token']):
                raise ValidationError({'token': ['Invalid value']})

            return attrs

        def save(self):
            return self.set_password_form.save()

    serializer_class = Serializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'status': 'ok', 'details': str(_('Password has been reset with the new password.'))},
        )


class PasswordChangeView(generics.GenericAPIView):
    class Serializer(serializers.Serializer):
        old_password = serializers.CharField(max_length=128)
        new_password = serializers.CharField(max_length=128)

        def validate(self, attrs):
            if not self.context['request'].user.check_password(attrs['old_password']) and not settings.DEBUG:
                raise serializers.ValidationError({'old_password': str(_('Incorrect password'))})
            try:
                password_validation.validate_password(attrs['new_password'])
            except DjangoValidationError as e:
                raise serializers.ValidationError({'new_password': e.messages})
            return attrs

        def save(self):
            request = self.context['request']
            u = request.user
            u.set_password(self.validated_data['new_password'])
            u.save()
            login(request, u)
            return self.instance

    serializer_class = Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'ok', 'details': str(_('Password has been changed'))}, status=status.HTTP_200_OK)
