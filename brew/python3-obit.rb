require "formula"

class Python3Obit < Formula
  homepage "http://www.jive.nl/jivewiki/doku.php?id=parseltongue:parseltongue"
  url "http://www.jive.nl/parseltongue/releases/Obit-27JUL20.tar.gz"
  sha256 "ed5fbba82b90859d9de51e0c4368136a6c92adb213b8b239c461344f3ceb90e6"

  depends_on "python@3.9"
  depends_on "glib"
  depends_on "gsl"
  depends_on "pkg-config"

  version "27JUL20"

  fails_with :clang do
    build 425
    cause "error in backend: Cannot select: intrinsic %llvm.x86.sse.cvtpi2ps"
  end

  patch do
    url "http://www.jive.nl/parseltongue/releases/obit-python3.patch"
    sha256 "43a208adf988cf58f33e1a1d52ca3952d31ad772cd60f9e518fccaca61d1e286"
  end

  patch :p3 do
    url "http://www.jive.nl/parseltongue/releases/obit-makesetup.patch"
    sha256 "aba59a9206a9ca2fcc3cf4521d175ff6011b98f957e56403b6665c9fb46b1ed2"
  end

  patch :p3 do
    url "http://www.jive.nl/parseltongue/releases/obit-sincos.patch"
    sha256 "6951151c3767a6e5a12a3ee5338d1f4ba6b42541f1d9883c8b419e0bd519a948"
  end

  def install
    ENV.deparallelize

    # The glib dependency can bring in python@3.12 or newer; make sure
    # we use python@3.9 for the build!
    ENV.prepend_create_path "PATH", Formula["python@3.9"].opt_libexec/"bin"

    system "./configure", "--prefix=#{prefix}", "CPPFLAGS=-Wno-implicit-function-declaration"
    system "make"
    (prefix+"python3").install Dir["python/*.py"]
    (prefix+"python3").install Dir["python/*.so"]
    (prefix+"python3").install Dir["python/*.egg/*.py"]
    (prefix+"python3").install Dir["python/*.egg/*.so"]
    system "unzip python/*.egg || true"
    (prefix+"python3").install Dir["_Obit.py"]
    (prefix+"python3").install Dir["_Obit.*.so"]
  end
end
