from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("zindex", ["zindex.pyx"]),]
# You can add directives for each extension too
# by attaching the `pyrex_directives`
for e in ext_modules:
    e.pyrex_directives = {"boundscheck": False}
setup(
    name = "Morton-order utilities",
    cmdclass = {"build_ext": build_ext},
    ext_modules = ext_modules
)
