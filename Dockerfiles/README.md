### Docker Instructions

1. Build docker image:

```{bash}
docker build -t neurodata/ndmg .
```

2. Launch docker instance:

```{bash}
docker run -ti neurodata/ndmg:latest 
```


To run `ndmg_bids`:
```
docker run -ti --name ndmg -v /Users/gkiar/Downloads/ds114/:${HOME}/data neurodata/ndmg -i ${HOME}/data/ -o ${HOME}/data/outputs -p 02 -s test
```
