-- Design stage for Appointment System (kite school)
-- Evaluate if we can reuse some component for booking and appointment systyem
-- shares client_id, status (client table, status enums and etc...)

-- TODO - sample data
-- define default timeslot (to be taken from UI input)
drop table if exists staff_default_timeslot;
create table staff_default_timeslot
(
	staff_id		int,    -- references staff(id),
    day_of_week     tinyint(3) unsigned DEFAULT '1',
    slot_time 		time
);

-- TODO - generate data from staff_default_timeslot for each week for given time range
-- should use SqlAlchemy, so we can generate staff calendar from UI
drop table if exists staff_calendar;
create table staff_calendar
(
    staff_id		int,
    datetime_		datetime,
    status			tinyint(3) NOT NULL DEFAULT '1'  -- available=1, unavailable=0, blocked=-1
    -- appointment_id	references appointment(id)
);


drop table if exists appointment;
create table appointment
(
	id				int,
    staff_id		int,    -- references staff(id),
    client_id		int,    -- references client(id),
    datetime_		datetime,
    status			int(3) NOT NULL DEFAULT '1'  -- CREATED, CONFIRMED, PAID, CANCELLED...
);
