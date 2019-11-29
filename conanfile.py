#!/usr/bin/python
# -*- coding: UTF-8 -*-

from conans import ConanFile, MSBuild, CMake, tools


class ChromiumbaseConan(ConanFile):
    name = "chromium-base"
    version = "1.0.2"
    license = ""
    author = "google"
    url = "https://github.com/shaoyuan1943/chromium-base"
    description = "Base library from chromium source code"
    topics = ("chromium", "base")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def configure(self):
        if self.settings.os == "Windows":
            self.generators = "visual_studio", # Trailing comma, or ["visual_studio"]
        else:
            self.generators = "cmake",  # Note the trailing comma

    def source(self):
        self.run("git clone -b conan https://github.com/243286065/chromium-base.git")
        if self.settings.os == "Linux":
            # 解决本身的依赖问题
            tools.replace_in_file("chromium-base/src/CMakeLists.txt", "project(base)",
                                '''project(base)
                include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                conan_basic_setup()''')

                        # 按照要求修改CMakeLists.txt
            tools.replace_in_file("chromium-base/src/CMakeLists.txt",
            '''set(BASE_INCLUDE_PLATFORM_DIRECTORIES   
        /usr/local/include/glib-2.0
        /usr/local/lib/glib-2.0/include # for glibconfig.h
    )''', "")
            # CMakeLists.txt默认是编译shared版本，需要根据配置自动选择
            if self.options.shared == False:
                tools.replace_in_file("chromium-base/src/CMakeLists.txt", "set(BASE_BUILD_CONFIGURATION_TYPE SHARED)",
                                '''set(BASE_BUILD_CONFIGURATION_TYPE)''')

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("glib/2.56.1@bincrafters/stable")
            self.requires("libevent/2.1.10@bincrafters/stable")
            self.options["glib"].shared = False
            self.options["libevent"].shared = False

    def build(self):
        if self.settings.os == "Linux":
            cmake = CMake(self)
            cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
            if self.settings.arch in ["x86_64", "x64"]:
                cmake.definitions["BASE_ARCH_PLATFORM"] = "x64"
            else:
                cmake.definitions["BASE_ARCH_PLATFORM"] = "x86"
            cmake.definitions["BASE_BUILD_PLATFORM"] = self.settings.os
            cmake.configure(source_folder="chromium-base/src")
            cmake.build()

        elif self.settings.os == "Windows":
            msbuild = MSBuild(self)
            msbuild.build("chromium-base/src/sln/base.sln", targets=["base"], build_type=self.settings.build_type)

    def package(self):
        self.copy("*", dst="include/base", src="chromium-base/src/base")
        self.copy("*", dst="include/build", src="chromium-base/src/build")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["base"]
