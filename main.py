import genshin
import asyncio
import os

friendlyGameName = {
    genshin.types.Game.HONKAI: "붕괴 3rd",
    genshin.types.Game.GENSHIN: '원신',
    genshin.types.Game.STARRAIL: "붕괴: 스타레일"
}

async def main():
    assert 'LTUID' in os.environ and 'LTOKEN' in os.environ, 'LTUID와 LTOKEN이 지정되지 않았습니다!'
    uIds = os.environ.get('LTUID').split(',')
    tokens = os.environ.get('LTOKEN').split(',')
    for index, uid in enumerate(uIds):
        cookies = {'ltuid': int(uid.strip()), 'ltoken': tokens[index].strip()}
        client = genshin.Client(cookies, lang='ko-kr')
        accounts = await client.get_game_accounts()
        print('====================================================')
        for account in accounts:
            if account.game not in friendlyGameName:
                continue
            print(f'{friendlyGameName[account.game]}({account.server_name}) - Lv.{account.level} {account.nickname}({account.uid})')
            reward, new = await claim_daily_reward(client, game=account.game)
            if reward is not None:
                if new is True:
                    print('출석 체크 완료!')
                else:
                    print('이미 출석 체크 된 계정입니다.')
                print(f'보상: {reward.name} x{reward.amount}')
            else:
                print('출석 체크에 실패했습니다.')
            print('====================================================')



async def claim_daily_reward(client: genshin.Client, game):
    signed_in, claimed_rewards = await client.get_reward_info(game=game)

    try:
        reward = await client.claim_daily_reward(game=game)
    except genshin.AlreadyClaimed:
        assert signed_in
        rewards = await client.get_monthly_rewards(game=game)
        return rewards[claimed_rewards], False
    except genshin.AccountNotFound:
        assert not signed_in
        return
    else:
        assert not signed_in

    rewards = await client.get_monthly_rewards(game=game)
    assert rewards[claimed_rewards].name == reward.name
    return reward, True

if __name__ == "__main__":
    asyncio.run(main())