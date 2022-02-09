CREATE INDEX IF NOT EXISTS cv_cv__attributes ON cv_cv USING GIN (attributes jsonb_path_ops);


-- DROP VIEW IF EXISTS v_cv_info;
CREATE OR REPLACE VIEW v_cv_info AS
    SELECT
        cv.id AS cv_id,
        rating.rating
    FROM
        cv_cv       AS cv
        LEFT JOIN (
                      SELECT
                          cv_id,
                          AVG( rating ) AS rating
                      FROM
                          main_requestrequirementcv
                      GROUP BY
                          cv_id
                  ) AS rating ON TRUE
            AND cv.id = rating.cv_id
;

-- SELECT * FROM v_cv_info