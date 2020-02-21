SELECT towns.name, COUNT(comments.id) FROM towns
JOIN comments ON towns.id=comments.towns_id
GROUP BY towns.name HAVING towns.region_id={};