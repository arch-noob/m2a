# Maintainer: Roman Vasilev <2rvasilev@live.ru>
pkgname=m2a
pkgver=0.0.1
pkgrel=1
pkgdesc="M2A Mail to Apprise Message Relay"
arch=('any')
url=
license=('custom')
groups=()
depends=()
optdepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=()
install=${pkgname}.install
changelog=
source=('m2a.py' 'm2a.service' 'm2a.yaml.example' 'm2a.install')
md5sums=('9a5629ee16bb9d74c112c50abb6adbb6'
         '4db2e9c1988faed295fa247e591110fd'
         '8499b4996f7f8db02603d59b259b2971'
         '6ee502e286e2c91559e4a9d637a8d528')

package() {
    install -Dm 0755 -t "${pkgdir}/usr/local/bin/" m2a.py 
    install -Dm 0644 -t "${pkgdir}/usr/lib/systemd/user/" m2a.service
    install -Dm 0644 -t "${pkgdir}/usr/share/m2a/" m2a.yaml.example
}

