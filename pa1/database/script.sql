create table data_type
(
    code varchar(20) not null
        constraint pk_data_type_code
            primary key
);

create table page_type
(
    code varchar(20) not null
        constraint pk_page_type_code
            primary key
);

create table site_ipaddr
(
    id          serial not null
        constraint site_ipaddr_pk
            primary key,
    ip_addr     varchar(100),
    last_access timestamp,
    delay       integer
);

create table site
(
    id              serial not null
        constraint pk_site_id
            primary key,
    domain          varchar(500),
    robots_content  text,
    sitemap_content text,
    site_ipaddr_id  integer
        constraint fk_site_ipaddr_id
            references site_ipaddr
);

create table page
(
    id               serial not null
        constraint pk_page_id
            primary key,
    site_id          integer
        constraint fk_page_site
            references site
            on delete restrict,
    page_type_code   varchar(20)
        constraint fk_page_page_type
            references page_type
            on delete restrict,
    url              varchar(3000)
        constraint unq_url_idx
            unique,
    html_content     text,
    http_status_code integer,
    accessed_time    timestamp,
    html_hash        varchar(1024)
);

create index idx_page_site_id
    on page (site_id);

create index idx_page_page_type_code
    on page (page_type_code);

create index page_html_hash_index
    on page (html_hash);

create table page_data
(
    id             serial not null
        constraint pk_page_data_id
            primary key,
    page_id        integer
        constraint fk_page_data_page
            references page
            on delete restrict,
    data_type_code varchar(20)
        constraint fk_page_data_data_type
            references data_type
            on delete restrict,
    data           bytea
);

create index idx_page_data_page_id
    on page_data (page_id);

create index idx_page_data_data_type_code
    on page_data (data_type_code);

create table image
(
    id            serial not null
        constraint pk_image_id
            primary key,
    page_id       integer
        constraint fk_image_page_data
            references page
            on delete restrict,
    filename      varchar(255),
    content_type  varchar(50),
    data          bytea,
    accessed_time timestamp
);

create index idx_image_page_id
    on image (page_id);

create table link
(
    from_page integer not null
        constraint fk_link_page
            references page
            on delete restrict,
    to_page   integer not null
        constraint fk_link_page_1
            references page
            on delete restrict,
    constraint _0
        primary key (from_page, to_page)
);

create index idx_link_from_page
    on link (from_page);

create index idx_link_to_page
    on link (to_page);


