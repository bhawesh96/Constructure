drop table players;

CREATE TABLE players (
  `id` BIGINT AUTO_INCREMENT,
  `name` VARCHAR(45),
  `reg_no` VARCHAR(45),
  `email` VARCHAR(45),
  `mobile` VARCHAR(10),
  `password` VARCHAR(200),
  `college` VARCHAR(20),
  `ques_asked` VARCHAR(40),  -- array of 1s and 0s specifiying which ques has been asked
  `curr_ques_id` VARCHAR(20), -- xx_yy format xx corresponds to the round number and yy corresponds to the ques no.
  `r1_res` VARCHAR(20),
  `r2_res` VARCHAR(20),
  `r3_res` VARCHAR(20),
  `r4_res` VARCHAR(20),
  `r5_res` VARCHAR(20),
  `r6_res` VARCHAR(20),
  `curr_trial` INT(5), -- tells which trial is he currently on. 0 for fresh
  PRIMARY KEY (`id`));

create table questions
(
  ques_id varchar(10) primary Key,
    question varchar(1000),
    op1 varchar(500),
    op2 varchar(500),
    op3 varchar(500),
    op4 varchar(500),
    ans varchar(10),
    point_wt varchar(10),
    moeny_wt varchar(10)
    
);

create table score
(
  user_id int references players(id),
    points int(100)
);
---CREATE PLAYER PROCEDURE
---SIGNS UP A USER IF NOT ALREADY EXISTS


drop procedure if exists `insert_player`;
delimiter $$
create procedure `insert_player`(  IN p_name VARCHAR(45), IN p_regno VARCHAR(45), IN p_email VARCHAR(45),IN p_mobile VARCHAR(10), IN p_password VARCHAR(200), IN p_college varchar(20))
begin
	if exists( SELECT ID FROM players WHERE  reg_no = p_regno) 
    then select 'Not unique';
	else
	insert into players(name,reg_no,email,mobile,password,college,ques_asked,curr_ques_id,r1_res,r2_res,r3_res,r4_res,r5_res,r6_res,curr_trial) values ( p_name,p_regno,p_email,p_mobile,p_password,p_college,'0','01_01',0,0,0,0,0,0,0);
	  end if;
end$$
delimiter ;

call insert_player('rahul','150911122','abc@gmail.com','9008318345','rahul123','MIT');
-- select @flag;

select * from players;

---VALIDATE LOGIN PROCEDURE
---RETURNS 0 IN THE VARIABLE PASSED IF NOT FOUND AND THE ID OF THE PLAYER IF FOUND



delimiter $$
create procedure civicq.validate_login(in e varchar(45), in p varchar(20))
begin
select * from players where email = e and password=p;
end
$$
delimiter ;


-- set val = ifnull(val,0);
call validate_login('abc@gmail.com','rahul13',@ans);

select @ans;





