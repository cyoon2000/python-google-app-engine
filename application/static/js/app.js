'use strict';
var myApp = angular.module('myApp', ['ngRoute']);


// TODO - Calendar Nav
// TODO - Refactor onSuccess/onFailure, Error Handling.


// GET returns availability for each unit for default date range (today + X days)
// POST updates availability for each cell (unit and date)
myApp.controller('mainController', function($scope, $attrs, $http) {
    $scope.documents = [];
    $scope.success = false;
    $scope.error = false;

    // Reference http://stackoverflow.com/questions/14523679/can-you-pass-parameters-to-an-angularjs-controller-on-creation
    if (!$attrs.unitid) throw new Error("No unitid for mainController");
    $scope.urlGet = "http://localhost:8080/bookings/availability/unit/" + $attrs.unitid;

    $scope.updateAvailability = function(data) {
        console.log("REQUEST updateAvailability (" + data.date_slot + ") id = " + data.id + " booked = " + data.booked);
        var json = {
                id: data.id,
                booked: data.booked
            }
        $http.post('http://localhost:8080/bookings/availability/'+ data.id, json)
            .then(
                function(json, status) {
                    //console.log("SUCCESS");
                    $scope.responsePOST = json.data;
                    console.log("RESPONSE updateAvailability (" + data.date_slot + ") id = " + data.id + " booked = " + data.booked);
                }
            )
    }

    $http.get($scope.urlGet)
        .then(
            function(result) {
                console.log("SUCCESS :  ", $scope.urlGet);
                $scope.documents = result.data;
                $scope.error = true;
            },
            // OnFailure function
            function(reason) {
                console.log("ERROR : ", $scope.urlGet)
                console.log(reason)
                $scope.somethingWrong = reason;
                $scope.error = true;
            }
        )
    });

// GET returns list of units for given resort
myApp.controller('resortController', function($scope, $attrs, $http) {
    $scope.units = [];
    $scope.success = false;
    $scope.error = false;

    // $scope.url = "http://localhost:8080/bookings/resorts/2/units";
    if (!$attrs.resortid) throw new Error("No resortid for resortController");
    $scope.url = "http://localhost:8080/bookings/resorts/" + $attrs.resortid + "/units";

    $http.get($scope.url)
        .then(
            function(result) {
                console.log("SUCCESS : ", $scope.url);
                $scope.units = result.data;
                $scope.error = true;
            },
            // OnFailure function
            function(reason) {
                console.log("ERROR : ", $scope.url)
                console.log(reason)
                $scope.somethingWrong = reason;
                $scope.error = true;
            }
        )
    });

// GET returns prev/next dates
myApp.controller('dateNavController', function($scope, $attrs, $http) {
    $scope.units = [];
    $scope.success = false;
    $scope.error = false;

    // place holder
    $scope.next = function(data) {
        $scope.url = "http://localhost:8080/bookings/calendar/" + $attrs.current + "?next";
        // call $http.get
    }
    $scope.prev = function(data) {
        $scope.url = "http://localhost:8080/bookings/calendar/" + $attrs.current + "?next";
        // call $http.get
    }
//    $http.get($scope.url)
//        .then(
//            function(result) {
//                console.log("SUCCESS : ", $scope.url);
//                $scope.dates = result.data;
//                $scope.error = true;
//            },
//            // OnFailure function
//            function(reason) {
//                console.log("ERROR : ", $scope.url)
//                console.log(reason)
//                $scope.somethingWrong = reason;
//                $scope.error = true;
//            }
//        )
    });

