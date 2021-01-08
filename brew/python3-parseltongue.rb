require "formula"

class Python3Parseltongue < Formula
  homepage "http://www.jive.nl/jivewiki/doku.php?id=parseltongue:parseltongue"
  url "http://www.jive.nl/parseltongue/releases/parseltongue-3.0.tar.gz"
  sha256 "3b2c159c105556550776558d97201b7b48c66b9e79863f75d1b382f6e548acc2"

  depends_on "python@3.9"
  depends_on "python3-obit"

  def install
    system "./configure", "--with-obit=#{HOMEBREW_PREFIX}/opt/python3-obit",
                          "--prefix=#{prefix}", "PYTHON=python3"
    system "make", "install"
  end
end
