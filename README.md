insert into posts(root_id, parent_id, post_id, content) values(1, 1, 1, "This is post");
insert into posts(root_id, parent_id, post_id, content) values(1, 1, 2, "This is the first comment");
insert into posts(root_id, parent_id, post_id, content) values(1, 2, 3, "This is a reply to the first comment");
insert into posts(root_id, parent_id, post_id, content) values(1, 2, 4, "This is another reply to the first comment");
insert into posts(root_id, parent_id, post_id, content) values(1, 4, 5, "This is a nested reply");
insert into posts(root_id, parent_id, post_id, content) values(1, 1, 6, "This is a second top-level comment");

insert into users(username, password) values("admin","password");

pragma foreign_keys=off;

delete from posts;
insert into posts(post_id, root_id, parent_id, username, content) values (1, 1, 1, "admin", "Root Post 1");
insert into posts(post_id, root_id, parent_id, username, content) values (2, 1, 1, "admin", "Comment on Post 1 (same level as Root Post 1)");
insert into posts(post_id, root_id, parent_id, username, content) values (3, 1, 2, "admin", "Comment on Post 2");
insert into posts(post_id, root_id, parent_id, username, content) values (4, 1, 3, "admin", "Root Post 2");
insert into posts(post_id, root_id, parent_id, username, content) values (5, 1, 4, "admin", "Comment on Post 4");
insert into posts(post_id, root_id, parent_id, username, content) values (6, 1, 2, "admin", "Comment on Post 5");

pragma foreign_keys=on;

## TODO
## ===============================
## [x] counting comments and showing under post
## [x] requires_auth
## [x] creating comment/post as logged user
## [ ] paging
## [ ] handle current date, deleted date
## [ ] validations
## [ ] load pictures
## [ ] truncate
## [ ] change/reset password (with email confirmation?)


select post_id, content from posts where post_id=root_id

select t1.root_id, t1.comment_count, t2.content, t2.username
from (select root_id, count(post_id) as comment_count from posts group by root_id) t1
left join (select root_id, content, username from posts) t2
on t1.root_id = t2.root_id
;


select t2.post_id, t2.content, t2.username, t1.comment_count from
(select root_id, count(post_id) as comment_count from posts group by root_id) t1
left join
(select post_id, content, username from posts) t2
on t1.root_id = t2.post_id
;





select t2.post_id, t1.comment_count, t2.content, t2.username from (select root_id, count(post_id) as comment_count from posts group by root_id) t1 left join (select post_id, content, username from posts) t2 on t1.root_id = t2.post_id

