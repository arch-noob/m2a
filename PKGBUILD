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
md5sums=('7764dbb4704e945939f184d7e35ed141'
         '24f517e7dd31ff6bdb6845fb143a7850'
         'fd81a11c88b526c78cfe63c3d87ea2be'
         '6ee502e286e2c91559e4a9d637a8d528')

package() {
    install -Dm 0755 -t "${pkgdir}/usr/local/bin/" m2a.py 
    install -Dm 0644 -t "${pkgdir}/usr/lib/systemd/user/" m2a.service
    install -Dm 0644 -t "${pkgdir}/usr/share/m2a/" m2a.yaml.example
}

