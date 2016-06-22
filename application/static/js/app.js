'use strict';
var myApp = angular.module('myApp', ['ngRoute']);
myApp.controller('mainController', function($scope, $attrs, $http) {
    $scope.documents = [];
    $scope.success = false;
    $scope.error = false;

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
                console.log("SUCCESS", $scope.urlGet);
                $scope.documents = result.data;
                $scope.error = true;
            },
            // OnFailure function
            function(reason) {
                console.log("ERROR", $scope.urlGet)
                console.log(reason)
                $scope.somethingWrong = reason;
                $scope.error = true;
            }
        )
    });

myApp.controller('resortController', function($scope, $attrs, $http) {
    $scope.units = [];
    $scope.success = false;
    $scope.error = false;

//    $scope.url = "http://localhost:8080/bookings/resorts/2/units";
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
                console.log("ERROR", $scope.url)
                console.log(reason)
                $scope.somethingWrong = reason;
                $scope.error = true;
            }
        )
    });