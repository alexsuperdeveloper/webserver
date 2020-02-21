SELECT comments.id,
regions.name AS region_name,
towns.name AS town_name,
user_name,
user_patronim,
user_last_name,
user_email,user_phone,
comment, pub_datetime FROM comments
JOIN regions ON regions.id=comments.region_id
JOIN towns ON towns.id=comments.towns_id
ORDER BY pub_datetime DESC;