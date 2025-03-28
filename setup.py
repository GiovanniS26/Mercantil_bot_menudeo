from distutils.core import setup
from Cython.Build import cythonize

setup(
    name="mercantil_bot",
    ext_modules=cythonize(["mercantil_bot.pyx"], compiler_directives={"language_level": 3})
)
