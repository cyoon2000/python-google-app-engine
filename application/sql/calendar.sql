drop table if exists calendar;
create table calendar
(
    date_       date        primary key
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

-- stored procedure : insert data to availability for given unit_id
drop procedure fill_unit_availability;

delimiter $$
create procedure fill_unit_availability(unit_id int, start_date date, end_date date)
begin
  declare date_ date;
  set date_=start_date;

  while date_ < end_date do
    	insert into availability values(date_, unit_id, NULL, 1);
    	set date_ = adddate(date_, interval 1 day);
	end while;
end $$
delimiter ;

call fill_unit_availability(277, '2016-07-01', '2016-07-31');