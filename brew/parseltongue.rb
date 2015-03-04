require "formula"

class Parseltongue < Formula
  homepage "http://www.jive.nl/jivewiki/doku.php?id=parseltongue:parseltongue"
  url "http://www.jive.nl/parseltongue/releases/parseltongue-2.1.tar.gz"
  sha1 "a36ce09ed3acdecdadfd78b0225829ebe8bc7a97"

  depends_on "obit"

  def install
    system "./configure", "--with-obit=#{HOMEBREW_PREFIX}/opt/obit",
                          "--prefix=#{prefix}"
    system "make", "install"
  end
end
