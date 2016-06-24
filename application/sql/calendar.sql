drop table if exists calendar;
create table calendar
(
    date_       date        primary key
);


-- stored procedure : insert data to calendar
drop procedure if exists fill_calendar;
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

call fill_calendar('2016-07-01', '2017-06-30');


---- NOTE : This has been migrated to SQLAlchemy
--drop table if exists availability;
--create table availability
--(
--    date_slot      	date        references calendar(date_),
--    unit_id         int         references unit(id),
--    booking_id		int			references booking(id),
--    status			tinyint(3) NOT NULL DEFAULT '1'  -- available=1, unavailable=0, blocked=-1
--);


---- NOTE : This has been migrated to SQLAlchemy
---- stored procedure : insert to data to unit_calendar for given unit_id
drop procedure if exists fill_availability;
delimiter $$
create procedure fill_availability(unit_id int, start_date date, end_date date)
begin
  declare date_ date;
  set date_=start_date;

  while date_ < end_date do
        -- created_on, updated_on, id, date_slot, status, unit_id, booking_id
    	insert into availability values(NOW(), NOW(), NULL, date_, 1, unit_id, NULL);
    	set date_ = adddate(date_, interval 1 day);
	end while;
end $$
delimiter ;

call fill_availability(10, '2016-07-01', '2017-07-01');
