#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Dana Christen
#
# This file is part of XpenseMate, a tool for managing shared expenses and
# hosted at https://github.com/danac/xpensemate.
#
# XpenseMate is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

class DBConfig:
    """
    This class holds the various configuration parameters that can be
    determined at runtime and is used by the factories.
    """
    
    #: The database backend engine to use, among the ones in
    #: :data:`xpensemate.db.proxy.DatabaseProxyFactory.proxy_module_dispatch`
    engine = "postgres"
    
    #: The database name
    database = "expense"
    
    #: The database user
    user = "xpensemate_function_invoker"
    
    #: The users's password
    password = "lambda"
    
    #: The interface implemented in the database, among the ones in
    #: :data:`xpensemate.db.interface.DatabaseInterfaceFactory.interface_class_dispatch`
    interface = "stored_functions"
    
    #: The character used as delimiter in concatenated strings returned from the database
    string_concat_delimiter = '|'
    
    
    
