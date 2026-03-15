# ai/faq.py

FAQ = {
    "what is opensox ai": "OpenSox AI is a platform that helps developers discover open-source projects and start contributing quickly.",

    "what does opensox ai do": "OpenSox helps developers find open-source repositories based on their skills, interests, and preferred technologies.",

    "who is opensox ai for": "OpenSox AI is designed for developers who want to start contributing to open-source projects.",

    "how does opensox ai work": "You choose your preferred languages and technologies, and OpenSox helps you discover relevant open-source projects.",

    "is opensox ai free": "Yes, OpenSox offers free features that help developers discover open-source projects.",

    "what is opensox pro": "OpenSox Pro is a premium version that provides mentorship, advanced filtering, and additional resources.",

    "how can i start contributing to open source": "You can start by choosing your preferred technologies on OpenSox and exploring recommended projects.",

    "what type of projects are on opensox": "OpenSox lists projects across areas like web development, AI, backend systems, machine learning, and more.",

    "can beginners use opensox": "Yes, OpenSox helps beginners find beginner-friendly open-source projects.",

    "does opensox help with gsoc": "Yes, OpenSox provides guidance and resources for open-source programs like Google Summer of Code.",

    "how are projects ranked on opensox": "Projects are ranked based on activity level, popularity, and relevance to your selected filters.",

    "can i filter projects by programming language": "Yes, OpenSox allows you to filter projects by programming languages and technologies.",

    "can i filter projects by difficulty": "Yes, OpenSox provides filters such as activity level, competition level, and project popularity.",

    "does opensox provide mentorship": "Yes, OpenSox Pro users can access mentorship and guidance for contributing to open source.",

    "does opensox provide learning resources": "Yes, OpenSox provides learning resources and guides to help developers succeed in open source.",

    "how long does it take to find a project on opensox": "With OpenSox search filters, developers can find suitable open-source projects within seconds.",

    "does opensox host the projects": "No, OpenSox helps you discover projects that are hosted on platforms like GitHub or GitLab.",

    "can i join the opensox community": "Yes, you can join the OpenSox community through their Discord and other developer channels.",

    "how can i contact opensox support": "You can contact the OpenSox team through email at hi@opensox.ai.",

    "what problem does opensox solve": "OpenSox helps developers quickly discover open-source projects that match their skills and interests."
}


def normalize(text: str):
    return text.lower().strip()


def check_faq(question: str):
    """
    Returns FAQ answer if a match is found.
    Otherwise returns None.
    """

    q = normalize(question)

    for key, answer in FAQ.items():
        if key in q:
            return answer

    return None