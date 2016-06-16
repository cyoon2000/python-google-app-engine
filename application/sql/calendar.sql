drop table if exists calendar;
create table calendar
(
    date_       date        primary key
);

drop table if exists unit_calendar;
create table unit_calendar
(
    date_slot      	date        references calendar(date_),
    unit_id         int         references unit(id),
    booking_id		int			references booking(id),
    status			tinyint(3) NOT NULL DEFAULT '1'  -- available=1, unavailable=0, blocked=-1
);


-- stored procedure : insert data to calendar
drop procedure fill_calendar;
delimiter $$
create procedure fill_calendar(start_date date, end_date date)
begin
  declare date_ date;
  set date_=start_date;
  while date_ < end_date do
    insert into calendar values(date_);
    set date_ = adddate(date_, interval 1 day);
  end while;
end $$
delimiter ;

call fill_calendar('2016-07-01', '2017-08-01');


-- stored procedure : insert to data to unit_calendar for given unit_id
drop procedure if exists fill_unit_calendar;
delimiter $$
create procedure fill_unit_calendar(unit_id int, start_date date, end_date date)
begin
  declare date_ date;
  set date_=start_date;

  while date_ < end_date do
    	insert into unit_calendar values(date_, unit_id, NULL, 1);
    	set date_ = adddate(date_, interval 1 day);
	end while;
end $$
delimiter ;

call fill_unit_calendar(277, '2016-07-01', '2016-07-31');
