insert into posts(root_id, parent_id, post_id, content) values(1, 1, 1, "This is post");
insert into posts(root_id, parent_id, post_id, content) values(1, 1, 2, "This is the first comment");
insert into posts(root_id, parent_id, post_id, content) values(1, 2, 3, "This is a reply to the first comment");
insert into posts(root_id, parent_id, post_id, content) values(1, 2, 4, "This is another reply to the first comment");
insert into posts(root_id, parent_id, post_id, content) values(1, 4, 5, "This is a nested reply");
insert into posts(root_id, parent_id, post_id, content) values(1, 1, 6, "This is a second top-level comment");


pragma foreign_keys=off;

delete from posts;
insert into posts(post_id, root_id, parent_id, content) values (1, 1, 1, "Root Post 1");
insert into posts(post_id, root_id, parent_id, content) values (2, 1, 1, "Comment on Post 1 (same level as Root Post 1)");
insert into posts(post_id, root_id, parent_id, content) values (3, 1, 2, "Comment on Post 2");
insert into posts(post_id, root_id, parent_id, content) values (4, 1, 3, "Root Post 2");
insert into posts(post_id, root_id, parent_id, content) values (5, 1, 4, "Comment on Post 4");
insert into posts(post_id, root_id, parent_id, content) values (6, 1, 2, "Comment on Post 5");

insert into users(username, password) values("admin","password");

pragma foreign_keys=on;

## TODO
## ===============================
## counting comments and showing under post
## paging
## handle current data, deleted date
## validations
## requires_auth
## load pictures
## truncate
## change/reset password (with email confirmation?)


select post_id, content from posts where post_id=root_id

select t2.root_id, t2.comment_count, t1.content
from (select root_id, content from posts group by root_id) t1
left join (select root_id, count(post_id) as comment_count from posts group by root_id) t2
on t1.root_id = t2.root_id
;


QUERY_SELECT_POSTS="select t2.root_id as root_id, t2.comment_count as comment_count, t1.content as content from (select root_id, content from posts group by root_id) t1 left join (select root_id, count(post_id) as comment_count from posts group by root_id) t2 on t1.root_id = t2.root_id"



