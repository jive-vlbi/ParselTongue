require "formula"

class Obit < Formula
  homepage "http://www.jive.nl/jivewiki/doku.php?id=parseltongue:parseltongue"
  url "http://www.jive.nl/parseltongue/releases/Obit-22JUN10h.tar.gz"
  sha1 "8facd4985eaeab39c65f26f0fb18de5c051a6609"

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
