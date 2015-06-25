require "formula"

class Obit < Formula
  homepage "http://www.jive.nl/jivewiki/doku.php?id=parseltongue:parseltongue"
  url "http://www.jive.nl/parseltongue/releases/Obit-22JUN10j.tar.gz"
  sha1 "a1f0124317b94cd86c3707d6f17bd446958b97f0"

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
