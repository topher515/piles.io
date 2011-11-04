npm install hashlib
#npm install mongodb
pushd node_modules
git clone https://github.com/christkv/node-mongodb-native/ mongodb
git checkout 4c1bda08484cf7913235cae56941e755518a766f
popd
npm install connect
npm install express
npm install underscore
npm install socket.io
npm install yaml
sudo npm install -g tamejs