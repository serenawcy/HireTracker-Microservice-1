create schema if not exists users;
use users;

drop table if exists user;
create table user
(
    user_id  int          not null AUTO_INCREMENT,
    nickname varchar(256) not null,
    email    varchar(256) not null,
    school   varchar(256) null,
    major    varchar(256) null,
    constraint user_pk
        primary key (user_id),
    constraint user_email
        unique (email)
);



insert into user (nickname, email, school, major)
values ('hahaha', 'hahaha04@gmail.com', 'Columbia University', 'Computer Science'),
       ('hihi', 'hihi10@gmail.com', 'Columbia University', NULL),
       ('ohoh', 'ohoh59@gmail.com', NULL, 'Computer Engineering');