'use strict';
angular.module('myApp', ['ngRoute'])
  .controller('mainController', function($scope, $http) {
    $scope.documents = [];
    $scope.success = false;
    $scope.error = false;

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

    $http.get('http://localhost:8080/bookings/availability/unit/11')
        .then(
            function(result) {
                console.log("SUCCESS");
                $scope.documents = result.data;
                $scope.error = true;
            },
            // OnFailure function
            function(reason) {
                console.log("ERROR")
                console.log(reason)
                $scope.somethingWrong = reason;
                $scope.error = true;
            }
        )
    });


