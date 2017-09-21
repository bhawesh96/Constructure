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

CREATE TABLE `civicq`.`score` (
  `user_id` BIGINT REFERENCES `players` (`user_id`),
  `points` BIGINT(20),
  `pres_ques_id` VARCHAR(20)
  );

CREATE TABLE `civicq`.`questions` (
  `ques_id` VARCHAR(20),
  `question` VARCHAR(400),
  `op1` VARCHAR(300),
  `op2` VARCHAR(300),
  `op3` VARCHAR(300),
  `op4` VARCHAR(300),
  
  PRIMARY KEY (`ques_id`));

---CREATE PLAYER PROCEDURE
---SIGNS UP A USER IF NOT ALREADY EXISTS


drop procedure if exists `insert_player`;
delimiter $$
create procedure `insert_player`(  IN p_name VARCHAR(45), IN p_regno VARCHAR(45), IN p_email VARCHAR(45),IN p_mobile VARCHAR(10), IN p_password VARCHAR(200), IN p_college varchar(20),OUT flag int)
begin
	if exists( SELECT ID FROM players WHERE  reg_no = p_regno) 
	then set flag =0;
    else
	insert into players(name,reg_no,email,mobile,password,college,ques_asked,curr_ques_id,r1_res,r2_res,r3_res,r4_res,r5_res,r6_res,curr_trial) values ( p_name,p_regno,p_email,p_mobile,p_password,p_college,'0','01_01',0,0,0,0,0,0,0);
	set flag=1;
    end if;
end$$
delimiter ;

call insert_player('rahul','150911122','abc@gmail.com','9008318345','rahul123','MIT',@flag);
select @flag;

select * from players;

---VALIDATE LOGIN PROCEDURE
---RETURNS 0 IN THE VARIABLE PASSED IF NOT FOUND AND THE ID OF THE PLAYER IF FOUND



delimiter $$
create procedure civicq.validate_login(in e varchar(45), in p varchar(20), out val int)
begin
select id into val from players where email = e and password=p;
set val = ifnull(val,0);
end
$$
delimiter ;


call validate_login('abc@gmail.com','rahul13',@ans);

select @ans;

