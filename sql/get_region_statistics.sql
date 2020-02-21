SELECT regions.id, regions.name, COUNT(comments.id) FROM comments
JOIN regions ON regions.id=comments.region_id
GROUP BY region_id
HAVING COUNT(comments.id)>5;

