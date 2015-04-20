
drop table if exists games;
drop table if exists moves;
create table games (
      id integer primary key autoincrement,
      starttime integer
);

create table moves (
    id integer primary key autoincrement,
    game integer,
    pos text not null
);
