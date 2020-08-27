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

bravia_test() {
    echo ">>> Run Sony Bravia Test"
    python -m unittest -v tests/test_sony_bravia.py
}

base_test() {
    echo ">>> Run Base Test"
    python -m unittest -v tests/test_base.py
}

gateway_test() {
    echo ">>> Run Gateway Test"
    python -m unittest -v tests/test_aqara_gateway.py
}


while [ "$1" != "" ]; do
    arg=$1;shift

    case ${arg} in 
        "sonoff") sonoff_test;;
        "yeelight") yeelight_test;;
        "aqara")aqara_test;;
        "gateway")gateway_test;;
        "bravia")bravia_test;;
        "base")base_test;;
        "all")
        sonoff_test &&
        yeelight_test &&
        aqara_test &&v echo "All Test Pass"
        ;;
    esac
done


