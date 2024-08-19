import os
from conans import ConanFile, tools

in_gitlab = False

version = "local_test"
tag = "release"

if "CI_BUILD_TAG" in os.environ:
    print ("use tag %s" % os.environ["CI_BUILD_TAG"])
    version = os.environ["CI_BUILD_TAG"]
    tag = version

if "GITLAB_CI" in os.environ and os.environ["GITLAB_CI"]:
    in_gitlab = True

class BrpcConan(ConanFile):
    name = "brpc"
    version = "%s" % version
    settings = "cppstd", "os", "compiler", "build_type", "arch"
    default_settings = "cppstd=17"
    options = {"shared": [True, False], "fPIC": [False, True], "tcmalloc": [False, True], "jemalloc": [False, True]}
    default_options = "shared=False", "fPIC=False", "tcmalloc=False", "jemalloc=True"
    generators = "cmake"
    exports_sources = "*"
    user = 'user'
    channel = 'stable'

    def configure(self):
        if self.options.tcmalloc == True and self.options.jemalloc == True:
            raise Exception("could not use tcmalloc and jemalloc together")

        if self.options.jemalloc:
            self.options["gperftools"].profiler_only = True
        else:
            self.options["gperftools"].profiler_only = False

    def requirements(self):
        self.requires("leveldb/1.20@%s/%s" % (self.user, self.channel))
        self.requires("gflags/2.2.1@%s/%s" % (self.user, self.channel))
        self.requires("openssl/1.1.1s@%s/%s" % (self.user, self.channel))
        self.requires("protobuf/3.15.8@%s/%s" % (self.user, self.channel))
        self.requires("zlib/1.2.13@%s/%s" % (self.user, self.channel))
        if self.options.tcmalloc or self.options.jemalloc:
            self.requires("gperftools/2.9.1@%s/%s" % (self.user, self.channel))
        if self.options.jemalloc:
            self.requires("jemalloc/5.3.0@%s/%s" % (self.user, self.channel))

        #self.requires("thrift/0.9.3@%s/%s" % (self.user, self.channel))

    @property
    def sourcedir(self):
        return "./"

    def build(self):
        with tools.chdir(self.sourcedir):
            headers = "%s" % os.path.join(self.deps_cpp_info["zlib"].rootpath, "include")
            libs = "%s " % os.path.join(self.deps_cpp_info["zlib"].rootpath, "lib")

            args = ["leveldb", "gflags", "openssl", "protobuf"]
            if self.options.tcmalloc or self.options.jemalloc:
                args.append("gperftools")
            if self.options.jemalloc:
                args.append("jemalloc")
            for k in args:
                dep = self.deps_cpp_info[k]
                headers += " %s " % os.path.join(dep.rootpath, "include")
                libs += " %s " % os.path.join(dep.rootpath, "lib")
                libs += " %s " % os.path.join(dep.rootpath, "bin")

            cmd = "STATICALLY_LINKED_protobuf=0 "
            cmd += "sh config_brpc.sh --headers=\"%s\" --libs=\"%s\"" % (headers, libs)
            self.output.info("configure brpc: %s" % cmd)
            self.run(cmd)
            make_args = "libbrpc.a output/include"
            if self.options.shared:
                make_args += " output/libbrpc.so "

            make_cmd = ""
            if self.options.jemalloc:
                make_cmd += "NEED_JEMALLOC=1 "
            if self.options.tcmalloc:
                make_cmd += "NEED_GPERFTOOLS=1 "
            make_cmd += "make %s -j%s" % (make_args, tools.cpu_count())
            self.output.info("make: %s" % make_cmd)
            self.run(make_cmd)
            self.run("mkdir -p output/lib && cp libbrpc.a output/lib")
        with tools.chdir(os.path.join(self.sourcedir, "tools", "rpc_replay")):
            self.run("make")
        with tools.chdir(os.path.join(self.sourcedir, "tools", "rpc_press")):
            self.run("make")

    def package(self):
        self.copy("*", "include/", os.path.join(self.sourcedir, "output", "include/"), keep_path=True)
        self.copy("*.a", "lib", self.sourcedir, keep_path=False)
        self.copy("*.so", "lib", self.sourcedir, keep_path=False)
        self.copy("rpc_replay", "bin/", os.path.join(self.sourcedir, "tools", "rpc_replay"), keep_path=False)
        self.copy("rpc_press", "bin/", os.path.join(self.sourcedir, "tools", "rpc_press"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["brpc"]
        self.cpp_info.cxxflags = ["-DBRPC_ENABLE_CPU_PROFILER", "-DBRPC_WITH_SHORT_FILE=1"]



