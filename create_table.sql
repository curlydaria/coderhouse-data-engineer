create table soldebenedet_coderhouse.products_new (
	_id varchar(25),
	title varchar(25),
	price float,
	createdAt timestamp,
	updatedAt timestamp,
	slug varchar(100),
	category__id varchar(25),
	category_name varchar(50),
	category_slug varchar(100),
	createdBy_role varchar(25),
	createdBy__id varchar(25),
	createdBy_name varchar(25),
	primary key(_id, createdAt)
	);