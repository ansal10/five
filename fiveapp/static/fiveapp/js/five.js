/**
 * Created by ansal on 4/6/17.
 */

var app = angular.module('fiveApp', []);

app.controller('ChatPanelIndexCtrl', function ($scope, $http, $interval) {
    var config = {
        headers:  {
            'Authorization': 'Basic YW5zYWwxMDphbnNhbDEw',
            'Content-Type': 'application/json'
        }
    };
    $scope.chatInSeconds = 0;


    $scope.refresh_data = function () {
        $http.get('/fiveapp/retrieve_users_and_chats', config).then( function success(response) {
        $scope.data = response.data.data;
        $scope.users_dict = {};
        $scope.chats_dict = {};
        $scope.chats_visible = [];
        for (var i = 0; i < $scope.data.users.length; i++) {
            var user = $scope.data.users[i];
            $scope.users_dict[user.user_uuid] = user;
        }
        for (var i = 0; i < $scope.data.chats.length; i++) {
            var chat = $scope.data.chats[i];
            $scope.chats_dict[chat.id] = chat;
        }
        $scope.chats_visible = $scope.data.chats.slice(0);
        $scope.available_users = $scope.data.users.slice(0);
        $scope.updateChatsAvailableList()


        }, function error(response) {
            $scope.error = response.data;

        });
    };

    $scope.refresh_data();

    $scope.userSelected = function (user_num, user_uuid) {
        if(user_num == 'userA'){
            $scope.userA = $scope.users_dict[user_uuid];
            $scope.userA.daysAvail = $scope.daysAvailable($scope.userA.filters);
        }else{
            $scope.userB = $scope.users_dict[user_uuid];
            $scope.userB.daysAvail = $scope.daysAvailable($scope.userB.filters);
        }
        $scope.checkCallFeasablity();
        $scope.updateChatsAvailableList();
        $scope.updateUsersAvailableList();

        // $scope.$apply();
    };

    $scope.updateUsersAvailableList = function () {
        function usersDaysCoincide(userA, user) {
            var days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
            for(var i = 0 ; i < days.length ; i++){
                if(userA.filters[days[i]]==true && user.filters[days[i]]==true){
                    return true;
                }
            }
            return false;
        }

        if($scope.userA != null){
            $scope.available_users = [];
            for(var i = 0 ; i < $scope.data.users.length; i++){
                if (usersDaysCoincide($scope.userA, $scope.data.users[i])){
                    $scope.available_users.push($scope.data.users[i]);
                }
            }
        }
    };
    $scope.checkCallFeasablity = function () {
        if($scope.userA!=null && $scope.userB != null){
            if($scope.chatInSeconds == null)
                $scope.chatInSeconds = 0;

            var userAMoment = moment().add($scope.chatInSeconds, 'seconds').tz($scope.userA.timezone);
            var userBMoment = moment().add($scope.chatInSeconds, 'seconds').tz($scope.userB.timezone);

            var userADay = userAMoment.format('dddd').toLowerCase();
            var userBDay = userBMoment.format('dddd').toLowerCase();

            var userAHour = userAMoment.format('HH:mm');
            var userBHour = userBMoment.format('HH:mm');

            if(
                ($scope.userA.filters[userADay] == true && userAHour >= $scope.userA.filters['minTime'] &&  userAHour < $scope.userA.filters['maxTime'] ) &&
                ($scope.userB.filters[userBDay] == true && userAHour >= $scope.userB.filters['minTime'] &&  userAHour < $scope.userB.filters['maxTime'] )
            ){
                $scope.schedulePossible = true;
            }else{
                $scope.schedulePossible = false;
            }
        }
    };

    $scope.daysAvailable = function (filters) {
      var b = [];
      var days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
      for(var i = 0 ; i < days.length ; i++){
          if(filters[days[i]]===true)
              b.push(days[i])
      }
      return b.join(" ");
    };

    $scope.updateChatsAvailableList = function () {
        var userA = $scope.userA;
        var userB = $scope.userB;
        if(userA || userB){
            $scope.chats_visible = [];

            for(i = 0 ; i < $scope.data.chats.length ; i++){
                var chat = $scope.data.chats[i];
                if((userA && !userB) && (chat.userA__user_uuid == userA.user_uuid || chat.userB__user_uuid == userA.user_uuid))
                    $scope.chats_visible.push(chat);
                else if((userB && !userA) && (chat.userA__user_uuid == userB.user_uuid || chat.userB__user_uuid == userB.user_uuid))
                    $scope.chats_visible.push(chat);
                else if ((userA && userB) && ((chat.userA__user_uuid==userA.user_uuid && chat.userB__user_uuid == userB.user_uuid) ||
                    (chat.userA__user_uuid==userB.user_uuid && chat.userB__user_uuid == userA.user_uuid))){
                    $scope.chats_visible.push(chat)
                }

            }
        }else{
            $scope.chats_visible = $scope.data.chats;
        }
    };

    $scope.userInfo = function (user_uuid) {
        return $scope.users_dict[user_uuid].user_uuid;
    };

    $scope.newChat = function () {
        var next_seconds = $scope.chatInSeconds;
        var userA = $scope.userA;
        var userB = $scope.userB;
        if (!userA || !userB ){
            alert("Invalid Params")
        }
        else{
            var data = {'usera_uuid':userA.user_uuid, 'userb_uuid':userB.user_uuid, 'next_seconds':next_seconds};
            $http.post('/fiveapp/update_chats', data, config ).then(function success(response) {
                alert('Chat created Successfully');
                $scope.refresh_data();
            }, function error(response) {
                alert( response.data.error || 'Some error occurred' );
                console.log(response.data)
            })
        }
    }

    $scope.resetPressed = function () {
        $scope.userA = null;
        $scope.userB = null;
        $scope.updateChatsAvailableList();
    }

    $scope.deleteChat = function (chat_id) {

        var data = {'chat_id':chat_id};
            $http.post('/fiveapp/update_chats', data, config ).then(function success(response) {
                alert('Chat Deleted Successfully');
                $scope.refresh_data();
            }, function error(response) {
                alert( response.data.error || 'Some error occurred' );
                console.log(response.data)
            })
    };

    $scope.$watch('chatInSecondsExpression', function () {
        $scope.chatInSeconds = eval($scope.chatInSecondsExpression)
    });

    $scope.$watch('chatInSeconds', function () {
       $scope.checkCallFeasablity();
    });

    $scope.$watch('apikey', function () {
       config = {
            headers:  {
                'Authorization': 'Basic '+$scope.apikey,
                'Content-Type': 'application/json'
            }
        }
    });



    $scope.setDisplayTime = function () {
        if($scope.userA!= null){
            var timezone = $scope.userA.timezone;
            $scope.userA.displayTime = moment().tz(timezone).format('dddd HH:mm:ss')
        }
        if($scope.userB!=null){
            var timezone = $scope.userA.timezone;
            $scope.userB.displayTime = moment().tz(timezone).format('dddd HH:mm:ss')
        }
    }


    $interval($scope.setDisplayTime, 1000);


} );


