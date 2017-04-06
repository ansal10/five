/**
 * Created by ansal on 4/6/17.
 */

var app = angular.module('fiveApp', []);

app.controller('ChatPanelIndexCtrl', function ($scope, $http) {
    var config = {
        headers:  {
            'Authorization': 'Basic YW5zYWwxMDphbnNhbDEw',
            'Content-Type': 'application/json'
        }
    };
    $scope.chat_in_seconds = 0;


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
        $scope.updateChatsAvailableList()


        }, function error(response) {
            $scope.error = response.data;

        });
    };

    $scope.refresh_data();

    $scope.userSelected = function (user_num, user_uuid) {
        if(user_num === 'userA'){
            $scope.userA = $scope.users_dict[user_uuid];
        }else{
            $scope.userB = $scope.users_dict[user_uuid];
        }
        $scope.updateChatsAvailableList();

        // $scope.$apply();
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

    $scope.newChat = function (next_seconds) {
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
    }

} );


