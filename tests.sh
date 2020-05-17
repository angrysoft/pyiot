#!/bin/sh

sonoff_test() {
    echo ">>> Run sonoff Test"
    python -m unittest -v tests/test_sonoff.py
}

yeelight_test() {
    echo ">>> Run Yeelight Test"
    python -m unittest -v tests/test_yeelight.py
}

aqara_test() {
    echo ">>> Run Aqara Test"
    python -m unittest -v tests/test_aqara.py
}

while [ "$1" != "" ]; do
    arg=$1;shift

    case ${arg} in 
        "sonoff") sonoff_test;;
        "yeelight") yeelight_test;;
        "aqara")aqara_test;;
    esac
done


