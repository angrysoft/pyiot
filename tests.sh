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

philips_test() {
    echo ">>> Run PhilipsBulb Test"
    python -m unittest -v tests/test_philipsbulb.py
}

print_tests() {
    tests=("sonoff" "yeelight" "aqara" "aqara_gateway" "bravia" "base" "philips" "all")
    for test in ${tests[@]}
    do
        echo ">>> $test"
    done
}


while [ "$1" != "" ]; do
    arg=$1;shift

    case ${arg} in 
        "sonoff") sonoff_test;;
        "yeelight") yeelight_test;;
        "aqara")aqara_test;;
        "aqara_gateway")gateway_test;;
        "bravia")bravia_test;;
        "base")base_test;;
        "philips")philips_test;;
        "all")
        sonoff_test &&
        yeelight_test &&
        aqara_test &&
        gateway_test &&
        bravia_test &&
        philips_test && echo "All Test Pass"
        ;;
        "list") print_tests;;
    esac
done


