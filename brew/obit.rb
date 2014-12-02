require "formula"

class Obit < Formula
  homepage "http://www.jive.nl/jivewiki/doku.php?id=parseltongue:parseltongue"
  url "http://www.jive.nl/parseltongue/releases/Obit-22JUN10g.tar.gz"
  sha1 "6a92aa15aa268722a3fb37f90f1e4183535e7568"

  depends_on "glib"
  depends_on "gsl"
  depends_on "pkg-config"

  fails_with :clang do
    build 425
    cause "error in backend: Cannot select: intrinsic %llvm.x86.sse.cvtpi2ps"
  end

  def install
    ENV.deparallelize

    system "./configure", "--prefix=#{prefix}"
    system "make"
    (prefix+"python").install Dir["python/*.py"]
    (prefix+"python").install Dir["python/*.so"]
  end
end
