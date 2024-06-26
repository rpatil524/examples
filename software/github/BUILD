#
# Copyright (C) 2022 Vaticle
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

java_binary(
    name = "github-bin-mac-x86_64",
    classpath_resources = ["//software/github/config/logback:logback-xml"],
    data = [
        "//software/github/datasets:github-data-json",
        "//software/github/schemas:github-data-schemas",
    ],
    main_class = "com.vaticle.typedb.example.software.github.view.GitApplication",
    runtime_deps = [
        "//software/github/view:view",
        "@maven//:org_jetbrains_skiko_skiko_awt_runtime_macos_x64",
    ],
)

java_binary(
    name = "github-bin-mac-arm64",
    classpath_resources = ["//software/github/config/logback:logback-xml"],
    data = [
        "//software/github/datasets:github-data-json",
        "//software/github/schemas:github-data-schemas",
    ],
    main_class = "com.vaticle.typedb.example.software.github.view.GitApplication",
    runtime_deps = [
        "//software/github/view:view",
        "@maven//:org_jetbrains_skiko_skiko_awt_runtime_macos_arm64",
    ],
)

java_binary(
    name = "github-bin-windows-x86_64",
    classpath_resources = ["//software/github/config/logback:logback-xml"],
    data = [
        "//software/github/datasets:github-data-json",
        "//software/github/schemas:github-data-schemas",
    ],
    main_class = "com.vaticle.typedb.example.software.github.view.GitApplication",
    runtime_deps = [
        "//software/github/view:view",
        "@maven//:org_jetbrains_skiko_skiko_awt_runtime_windows_x64",
    ],
)

java_binary(
    name = "github-bin-linux-x86_64",
    classpath_resources = ["//software/github/config/logback:logback-xml"],
    data = [
        "//software/github/datasets:github-data-json",
        "//software/github/schemas:github-data-schemas",
    ],
    main_class = "com.vaticle.typedb.example.software.github.view.GitApplication",
    runtime_deps = [
        "//software/github/view:view",
        "@maven//:org_jetbrains_skiko_skiko_awt_runtime_linux_x64",
    ],
)

java_binary(
    name = "github-bin-linux-arm64",
    classpath_resources = ["//software/github/config/logback:logback-xml"],
    data = [
        "//software/github/datasets:github-data-json",
        "//software/github/schemas:github-data-schemas",
    ],
    main_class = "com.vaticle.typedb.example.software.github.view.GitApplication",
    runtime_deps = [
        "//software/github/view:view",
        "@maven//:org_jetbrains_skiko_skiko_awt_runtime_linux_arm64",
    ],
)

load("@vaticle_dependencies//tool/checkstyle:rules.bzl", "checkstyle_test")
checkstyle_test(
    name = "checkstyle",
    include = glob(["*", ".factory/*"]),
    exclude = ["screenshots/interface.png", "README.md"],
    license_type = "apache-header",
    size = "small",
)
