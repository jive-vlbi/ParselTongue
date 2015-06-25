require "formula"

class Parseltongue < Formula
  homepage "http://www.jive.nl/jivewiki/doku.php?id=parseltongue:parseltongue"
  url "http://www.jive.nl/parseltongue/releases/parseltongue-2.2.tar.gz"
  sha1 "38bc93c0057e1864af9752a641d13e501cc87209"

  depends_on "obit"

  def install
    system "./configure", "--with-obit=#{HOMEBREW_PREFIX}/opt/obit",
                          "--prefix=#{prefix}"
    system "make", "install"
  end
end
