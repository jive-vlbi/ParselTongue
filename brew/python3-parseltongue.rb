require "formula"

class Python3Parseltongue < Formula
  homepage "http://www.jive.nl/jivewiki/doku.php?id=parseltongue:parseltongue"
  url "http://www.jive.nl/parseltongue/releases/parseltongue-2.97.tar.gz"
  sha256 "f1e325b6b0fce739a9370ec94a04c2151086f567472086c26c0fe9dd59785b6b"

  depends_on "python@3.9"
  depends_on "python3-obit"

  def install
    system "./configure", "--with-obit=#{HOMEBREW_PREFIX}/opt/python3-obit",
                          "--prefix=#{prefix}", "PYTHON=python3"
    system "make", "install"
  end
end
