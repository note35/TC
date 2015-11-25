echo 'flushdb' | sudo redis-cli
echo "hset user \"golden-tester\" \"{\'username\': u\'golden-tester\', \'password\': \'38815b4de919c2b5e42fda2297a2cdee62bea5897435eb9d386eabf1\', \'uid\': 1, \'regtime\': \'2015-11-25 15:32:06\'}\"" | sudo redis-cli 
py.test --cov-config .coveragerc --cov=../../TC --cov-report term-missing
