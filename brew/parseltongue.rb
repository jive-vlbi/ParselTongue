require "formula"

class Parseltongue < Formula
  homepage "http://www.jive.nl/jivewiki/doku.php?id=parseltongue:parseltongue"
  url "http://www.jive.nl/parseltongue/releases/parseltongue-2.3.tar.gz"
  sha256 "acc335d85dad8a5996ab4eb1088f5aa28a0e67278a20c002fde43956ded0d6db"

  depends_on "obit"

  def install
    system "./configure", "--with-obit=#{HOMEBREW_PREFIX}/opt/obit",
                          "--prefix=#{prefix}"
    system "make", "install"
  end
end
