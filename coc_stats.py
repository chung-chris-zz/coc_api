from cocapi import cocapi
import json
import re
import pandas as pd
import datetime


def read_json():
    """
    Get token and clan tag from json file
    """
    json_file = open('api_token.json')
    json_str = json_file.read()
    json_data = json.loads(json_str)

    token = json_data['token']
    clan_tag_str = json_data['clan_tag']
    
    return token, clan_tag_str


def check_tag(tag, tag_type):
    """
    Check and cleanse tag
    """
    if tag[:1] == '#':
        tag = tag[1:]
    
    if tag_type == 'clan':
        pattern = re.compile('[A-Z0-9]{8}')
    elif tag_type == 'war':
        pattern = re.compile('[A-Z0-9]{9}')

    match = pattern.match(tag)
    if match:
        return tag
    else:
        print('Check tag - incorrect')


def war_matchups(api, rounds, clan_tag_str):
    """
    Find war tags that clan_tag is in
    """
    war_list = []
    clan_tag_str = f'#{clan_tag_str}'
    for round in rounds:
        war_tags = round['warTags']
        for war_tag in war_tags:
            war_tag = check_tag(war_tag, 'war')
            r = api.cwl_war(war_tag)
            try:
                clan = r['clan']['tag']
            except:
                clan = None
            try:
                opponent = r['opponent']['tag']
            except:
                opponent = None
            if clan == clan_tag_str:
                war_list.append([war_tag, 'clan'])
            elif opponent == clan_tag_str:
                war_list.append([war_tag, 'opponent'])
    
    return war_list


def war_list_iterator(api, war_list):
    """
    Iterate over each war in war_list to produce dataframe
    Calls helper functions war_dict and war_to_df below
    """
    df = pd.DataFrame()
    for i, value in enumerate(war_list):
        war_num = i + 1
        war_summary = value
        members, clan_name, clan_tag_str, opp_tag, opp_name = war_dict(api, war_summary)
        df_war = war_to_df(members, clan_name, clan_tag_str, opp_tag, opp_name, war_num)
        df = df.append(df_war)
    
    return df


def war_dict(api, war_summary):
    """
    Helper function used in war_list_iterator function
    Convert single war's stats into dictionary
    """
    war_tag = war_summary[0]
    team = war_summary[1]
    if team == 'clan':
        opponent = 'opponent'
    else:
        opponent = 'clan'
    
    r = api.cwl_war(war_tag)

    opp_data = r[opponent]
    opp_tag = opp_data['tag']
    opp_name = opp_data['name']

    clan_data = r[team]
    clan_name = clan_data['name']
    clan_tag_str = clan_data['tag']
    members = clan_data['members']

    return members, clan_name, clan_tag_str, opp_tag, opp_name


def war_to_df(members, clan_name, clan_tag_str, opp_tag, opp_name, war_num):
    """
    Helper function used in war_list_iterator function
    Convert war_dict information to df
    """
    df_war = pd.DataFrame(members)
    for i, r in df_war.iterrows():
        # retreive info from attacks column
        attacks = r['attacks']
        try:
            attacks = attacks[0]
            defender_tag = attacks['defenderTag']
            stars = attacks['stars']
            percent = attacks['destructionPercentage']
            order = attacks['order']
            # add this info as new columns
            df_war.at[i, 'attack_opponent'] = defender_tag
            df_war.at[i, 'attack_stars'] = stars
            df_war.at[i, 'attack_percent'] = percent
            df_war.at[i, 'attack_order'] = order
        except:
            pass

        # retrieve info from bestOpponentAttack column
        opp = r['bestOpponentAttack']
        try:
            opp_tag = opp['attackerTag']
            opp_stars = opp['stars']
            opp_percent = opp['destructionPercentage']
            opp_order = opp['order']
            # add this info as new columns
            df_war.at[i, 'defense_opponent'] = opp_tag
            df_war.at[i, 'defense_stars'] = opp_stars
            df_war.at[i, 'defense_percent'] = opp_percent
            df_war.at[i, 'defense_order'] = opp_order
        except:
            pass
        
    # remove unnecessary cols, add war opponent, rename, reorder
    df_war.drop(['attacks','bestOpponentAttack'], axis=1, inplace=True)
    df_war['war_num'] = war_num
    df_war['clan_name'] = clan_name
    df_war['clan_tag'] = clan_tag_str
    df_war['opponent_clan_tag'] = opp_tag
    df_war['opponent_clan_name'] = opp_name
    df_war = df_war.rename(columns={'tag':'player_tag','name':'player_name',
                            'townhallLevel':'townhall_lvl','mapPosition':'map_position',
                            'opponentAttacks':'defenses'})
    cols = ['war_num','clan_name','clan_tag','opponent_clan_name','opponent_clan_tag',
            'map_position','player_name','player_tag','townhall_lvl',
            'attack_opponent','attack_stars','attack_percent',
            'attack_order','defenses','defense_opponent','defense_stars',
            'defense_percent','defense_order']
    df_war = df_war[cols]
    df_war = df_war.sort_values('map_position')

    return df_war


def get_timestamp():
    """
    Provide timestamp
    """
    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    return now


def main():
    """
    Main script
    """
    print('Beginning program...')
    # get token and clan_tag from json
    token, clan_tag_str = read_json()
    clan_tag_str = check_tag(clan_tag_str, 'clan')
    print('json file successfully read')

    # determine clan tag matchups
    api = cocapi(token, clan_tag_str)
    rounds = api.clan_leaguegroup()['rounds']
    print('API connection established')
    
    # get war tags that clan was in
    war_list = war_matchups(api, rounds, clan_tag_str)
    print('CWL matchups gathered')

    # produce dataframe from war_list and performing api calls
    df = war_list_iterator(api, war_list)
    print('API requests received and transformed')

    # save to excel
    clan_name = api.clan_tag()['name']
    now = get_timestamp()
    f_name = f'{now} {clan_name} CWL Stats.xlsx'
    df.to_excel(f_name, index=False)

    print(f'{f_name} produced.')
    input('Close to quit...')


if __name__ == "__main__":
    main()