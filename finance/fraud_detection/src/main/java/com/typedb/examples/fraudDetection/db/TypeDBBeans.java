/*
 * Copyright (C) 2022 Vaticle
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package com.typedb.examples.fraudDetection.db;

import com.vaticle.typedb.driver.TypeDB;
import com.vaticle.typedb.driver.api.TypeDBDriver;
import javax.enterprise.context.ApplicationScoped;
import javax.enterprise.inject.Disposes;
import javax.enterprise.inject.Produces;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

public class TypeDBBeans {

  private static final Logger LOGGER = Logger.getLogger(TypeDBBeans.class);

  @ConfigProperty(name = "typedb.host", defaultValue="localhost")
  String host;
  @ConfigProperty(name = "typedb.port", defaultValue="1729")
  String port;

  @Produces
  @ApplicationScoped
  TypeDBDriver getDriver() {

    LOGGER.info("Creating TypeDB driver");

    return TypeDB.coreDriver(host + ":" + port);
  }

   void closeDriver(@Disposes TypeDBDriver driver) {

     LOGGER.info("Closing TypeDB driver");

     driver.close();
   }
}
