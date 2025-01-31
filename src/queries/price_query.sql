SELECT 
    cp.name as part_name,
    cp.price,
    cp.updated_at as last_updated
FROM `{dataset_id}.car_parts` cp
JOIN `{dataset_id}.car_years` cy ON cp.car_year_id = cy.id
JOIN `{dataset_id}.car_models` mdl ON cy.model_id = mdl.id
JOIN `{dataset_id}.car_makes` m ON mdl.make_id = m.id
WHERE LOWER(m.name) = LOWER(@make)
AND LOWER(mdl.name) = LOWER(@model)
AND cy.year = @year
AND LOWER(cp.name) = LOWER(@part)
AND LOWER(cp.condition) = LOWER(@condition)
LIMIT 1