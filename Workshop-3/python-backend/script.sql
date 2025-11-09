CREATE TYPE user_type AS ENUM (
    'MACHINE REGISTER',
    'HUMAN REGISTER'
);

create table userp(
	idUser varchar(15) primary key,
	username  varchar(30) not null,
	password varchar(35) not null,
	type user_type not null
);

CREATE TYPE vehicle_type AS ENUM (
    'CAR',
    'MOTORCYCLE',
    'TRUCK',
    'BUS',
    'VAN',
    'SUV',
    'BICYCLE',
    'ELECTRIC BICYCLE',
    'ELECTRIC SCOOTER'
);

create table vehicle(
	licenseplate varchar(10) primary key,
	type vehicle_type not null,
	dateRegistered date not null
);

create table fee(
	idFee varchar(10) primary key,
	descFee varchar(255) not null,
	type vehicle_type not null,
	priceFee float not null
);

create table ticket(
	ticketid serial primary  key,
	ownerdoc varchar(15) not null,
	entry date not null,
	exit date,
	licenseplate varchar(10) not null,
	idFee varchar(10) not null,
	idUser varchar(15) not null,
	constraint Vehicle_fk foreign key(licenseplate) references vehicle(licenseplate),
	constraint Fee_FK foreign key(idFee) references fee(idFee),
	constraint User_FK foreign key(idUser) references userp(idUser)
);

create table payment(
	idpayment serial not null,
	ticketid integer not null,
	datepayment date not null,
	payment float not null,
	primary key (idpayment,ticketid),
	constraint Ticket_FK foreign key(ticketid) references ticket(ticketid)
);

create table lotSpace( 
	idLotSpace varchar(10),
	type vehicle_type not null,
	totalSpace integer not null
);
