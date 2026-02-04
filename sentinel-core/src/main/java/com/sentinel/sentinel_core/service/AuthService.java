package com.sentinel.sentinel_core.service;

import com.sentinel.sentinel_core.model.User;
import com.sentinel.sentinel_core.repository.UserRepository;
import org.springframework.stereotype.Service;
import java.util.UUID;

@Service
public class AuthService {

    private final UserRepository userRepository;

    public AuthService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User syncUser(String auth0Id, String email, String fullName) {
        return userRepository.findByAuthProviderId(auth0Id)
            .map(existingUser -> {
                existingUser.setFullName(fullName);
                return userRepository.save(existingUser);
            })
            .orElseGet(() -> {
                User newUser = new User();
                newUser.setAuthProviderId(auth0Id);
                newUser.setEmail(email);
                newUser.setFullName(fullName);
                return userRepository.save(newUser);
            });
    }
}