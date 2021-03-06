-- Copyright 2014 Dana Christen
--
-- This file is part of XpenseMate, a tool for managing shared expenses and
-- hosted at https://github.com/danac/xpensemate.
--
-- XpenseMate is free software: you can redistribute it and/or modify
-- it under the terms of the GNU Affero General Public License as
-- published by the Free Software Foundation, either version 3 of the
-- License, or (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU Affero General Public License for more details.
--
-- You should have received a copy of the GNU Affero General Public License
-- along with this program. If not, see <http://www.gnu.org/licenses/>.
--


--
-- TRIGGER FUNCTIONS
--

CREATE OR REPLACE FUNCTION check_expense_member_group()
  RETURNS TRIGGER AS
$BODY$
DECLARE
    member_exists BOOLEAN;
BEGIN
    member_exists := (
        SELECT EXISTS (
            SELECT *
            FROM table_member_group
            INNER JOIN table_expense ON table_expense.id = NEW.expense_id
            WHERE table_member_group.group_id = table_expense.group_id
                AND table_member_group.member_id = NEW.member_id
        )
    );
                
    IF member_exists IS TRUE THEN
      RETURN NEW;
    ELSE 
      RAISE EXCEPTION 'Member not in expense group';
    END IF;
END;
$BODY$
LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION check_expense_maker()
    RETURNS TRIGGER AS
    $BODY$
        DECLARE
            num_makers INTEGER;
            num_members INTEGER;
        BEGIN
            num_members := (
                SELECT COUNT(*)
                FROM table_expense_member
                WHERE table_expense_member.expense_id = NEW.expense_id
            );
            num_makers := (
                SELECT COUNT(*)
                FROM table_expense_member
                WHERE table_expense_member.expense_id = NEW.expense_id
                    AND table_expense_member.made_expense = TRUE
            );
                        
            IF NEW.made_expense IS FALSE AND num_members = 0 THEN
                RAISE EXCEPTION 'First member of an expense must have made it';
            END IF;
            
            IF NEW.made_expense IS TRUE and num_makers > 0 THEN
                RAISE EXCEPTION 'Expense maker already defined';
            END IF;
            
            RETURN NEW;
        END;
    $BODY$
    LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION check_group_owner()
    RETURNS TRIGGER AS
    $BODY$
        DECLARE
            num_owners INTEGER;
            num_members INTEGER;
        BEGIN
            num_members := (
                SELECT COUNT(*)
                FROM table_member_group
                WHERE table_member_group.group_id = NEW.group_id
            );
            num_owners := (
                SELECT COUNT(*)
                FROM table_member_group
                WHERE table_member_group.group_id = NEW.group_id
                    AND table_member_group.is_owner = TRUE
            );
                  
            IF NEW.is_owner IS FALSE AND num_members = 0 THEN
                RAISE EXCEPTION 'First member of a group must be owner';
            END IF;
            
            IF NEW.is_owner IS TRUE and num_owners > 0 THEN
                RAISE EXCEPTION 'Group already owned';
            END IF;
            
            RETURN NEW;
        END;
    $BODY$
    LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION check_transfer_member_group()
  RETURNS TRIGGER AS
$BODY$
DECLARE
    from_member_exists BOOLEAN;
    to_member_exists BOOLEAN;
BEGIN
    from_member_exists := (
        SELECT EXISTS (
            SELECT *
            FROM table_member_group
            WHERE table_member_group.group_id = NEW.group_id
                AND table_member_group.member_id = NEW.from_member_id
        )
    );
    to_member_exists := (
        SELECT EXISTS (
            SELECT *
            FROM table_member_group
            WHERE table_member_group.group_id = NEW.group_id
                AND table_member_group.member_id = NEW.to_member_id
        )
    );
                
    IF from_member_exists IS TRUE AND to_member_exists IS TRUE THEN
      RETURN NEW;
    ELSE 
      RAISE EXCEPTION 'Members of the transfer are not both in transfer group';
    END IF;
END;
$BODY$
LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION check_distinct_to_from_members()
  RETURNS TRIGGER AS
$BODY$
BEGIN
    IF NEW.from_member_id <> NEW.to_member_id THEN
        RETURN NEW;
    ELSE
        RAISE EXCEPTION 'A transfer must involve two different members';
    END IF;
END;
$BODY$
LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION check_amount_multiple_of_smallest_unit()
  RETURNS TRIGGER AS
$BODY$
DECLARE
    smallest_unit NUMERIC;
BEGIN
    smallest_unit := (SELECT table_group.smallest_unit FROM table_group WHERE table_group.id = NEW.group_id);
    IF NEW.amount - ROUND(NEW.amount / smallest_unit) * smallest_unit = 0 THEN
        RETURN NEW;
    ELSE
        RAISE EXCEPTION 'The amount is not a multiple of the smallest unit.';
    END IF;
END;
$BODY$
LANGUAGE 'plpgsql';


--
-- TRIGGER DEFINITIONS
--

DROP TRIGGER IF EXISTS check_expense_multiple_of_smallest_unit ON table_expense;
CREATE TRIGGER check_expense_multiple_of_smallest_unit
    BEFORE INSERT OR UPDATE
    ON table_expense 
    FOR EACH ROW
    EXECUTE PROCEDURE check_amount_multiple_of_smallest_unit();

DROP TRIGGER IF EXISTS check_expense_member_group ON table_expense_member;
CREATE TRIGGER check_expense_member_group
    BEFORE INSERT OR UPDATE
    ON table_expense_member 
    FOR EACH ROW
    EXECUTE PROCEDURE check_expense_member_group();

DROP TRIGGER IF EXISTS check_expense_maker ON table_expense_member;
CREATE TRIGGER check_expense_maker
    BEFORE INSERT OR UPDATE
    ON table_expense_member 
    FOR EACH ROW
    EXECUTE PROCEDURE check_expense_maker();

DROP TRIGGER IF EXISTS check_group_owner ON table_member_group;
CREATE TRIGGER check_group_owner
    BEFORE INSERT OR UPDATE
    ON table_member_group 
    FOR EACH ROW
    EXECUTE PROCEDURE check_group_owner();

DROP TRIGGER IF EXISTS check_transfer_multiple_of_smallest_unit ON table_transfer;
CREATE TRIGGER check_transfer_multiple_of_smallest_unit
    BEFORE INSERT OR UPDATE
    ON table_transfer 
    FOR EACH ROW
    EXECUTE PROCEDURE check_amount_multiple_of_smallest_unit();
    
DROP TRIGGER IF EXISTS check_transfer_member_group ON table_transfer;
CREATE TRIGGER check_transfer_member_group
    BEFORE INSERT OR UPDATE
    ON table_transfer
    FOR EACH ROW
    EXECUTE PROCEDURE check_transfer_member_group();
    
DROP TRIGGER IF EXISTS check_distinct_to_from_members ON table_transfer;
CREATE TRIGGER check_distinct_to_from_members
    BEFORE INSERT OR UPDATE
    ON table_transfer
    FOR EACH ROW
    EXECUTE PROCEDURE check_distinct_to_from_members();
