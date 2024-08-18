pragma foreign_keys=off;

delete from posts;
insert into posts(post_id, root_id, parent_id, content) values (1, 1, 1, "Root Post 1");
insert into posts(post_id, root_id, parent_id, content) values (2, 1, 1, "Comment on Post 1 (same level as Root Post 1)");
insert into posts(post_id, root_id, parent_id, content) values (3, 1, 2, "Comment on Post 2");
insert into posts(post_id, root_id, parent_id, content) values (4, 1, 3, "Root Post 2");
insert into posts(post_id, root_id, parent_id, content) values (5, 1, 4, "Comment on Post 4");
insert into posts(post_id, root_id, parent_id, content) values (6, 1, 2, "Another comment on Post 2");

insert into users(username, password) values("admin","password");

pragma foreign_keys=on;

## TODO
## ===============================
## [x] counting comments and showing under post
## [x] requires_auth
## [ ] creating comment/post as logged user
## [ ] paging
## [ ] handle current date, deleted date
## [ ] validations
## [ ] load pictures
## [ ] truncate
## [ ] change/reset password (with email confirmation?)




